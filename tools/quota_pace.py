#!/usr/bin/env python3
"""Read the installed quota CLI and conservatively gate one expensive action.

No credentials are read here. Only sanitized account windows are cached in
the ignored .local directory. Polls are separated by at least five minutes.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.local/quota-window-cache.json'


def read_cli(timeout_seconds=10):
    """Bound the entire CLI process group; a timed-out poll cannot linger."""
    process=subprocess.Popen(['quota','--json'],stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,text=True,start_new_session=True)
    try:
        stdout,_=process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        raise RuntimeError(f'Quota CLI exceeded {timeout_seconds}s; poll process group stopped')
    if process.returncode:
        # CLI stderr may contain account/provider details: do not publish it.
        raise RuntimeError('Quota CLI failed; no fresh allowance established')
    return json.loads(stdout)


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def duration(value):
    m = re.fullmatch(r'P(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?', value)
    if not m:
        raise ValueError('Unsupported quota-window duration')
    return sum(float(x or 0)*unit for x, unit in zip(m.groups(), [86400,3600,60,1]))


def evaluate(snapshot, now, deadline=None, tolerance=.03):
    if deadline and now >= deadline:
        return {'allowed':False, 'reason':'Campaign deadline reached', 'next_eligible_at':None, 'windows':[]}
    if not snapshot.get('provider_allowed', False):
        exhausted=[timestamp(w['resets_at'])+timedelta(seconds=60)
                   for w in snapshot.get('windows',[])
                   if w.get('resets_at') and (float(w.get('used') or 0)>=1 or w.get('locked_reason'))]
        wake=max(exhausted) if exhausted else None
        return {'allowed':False, 'reason':'Provider reports no available allowance',
                'next_eligible_at':wake.isoformat() if wake else None, 'windows':[]}
    rows, wakes, reasons = [], [], []
    for window in snapshot['windows']:
        length = duration(window['length'])
        used = float(window['used'])
        reset = timestamp(window['resets_at']) if window.get('resets_at') else None
        kind = window.get('kind',{}).get('kind')
        if used >= 1 or window.get('locked_reason'):
            reasons.append('An account window is exhausted or locked')
            if reset:
                wakes.append(reset+timedelta(seconds=60))
        if not length or not reset:
            continue
        # A past reset with stale pre-reset usage is not fresh allowance.
        if now >= reset:
            reasons.append('Reset crossed; a fresh CLI sample is required')
            wakes.append(now+timedelta(minutes=5))
            continue
        target = max(0., min(1., 1-(reset-now).total_seconds()/length))
        row = {'kind':kind, 'used':used, 'time_pace':target,
               'hard_tolerance_ceiling':min(1.,target+tolerance),
               'remaining':1-used, 'resets_at':reset.isoformat()}
        # Weekly pacing determines sustainable work. Never plan to spend the
        # tolerance itself: leaving its three points absorbs quantization,
        # concurrent account use and a single action's unmeasured cost.
        if kind in ('weekly','weekly_model'):
            if used > target:
                reasons.append('Weekly usage is ahead of its time-based pace')
                wakes.append(reset-timedelta(seconds=length*(1-used))+timedelta(seconds=60))
            if 1-used < .05:
                reasons.append('Preserving the last five percent until reset')
                wakes.append(reset+timedelta(seconds=60))
        elif 1-used < .05:
            reasons.append('A short/model window has less than five percent remaining')
            wakes.append(reset+timedelta(seconds=60))
        rows.append(row)
    if not rows:
        reasons.append('No measurable quota window')
    wake = max(wakes) if wakes else None
    if deadline and wake and wake >= deadline:
        reason = '; '.join(dict.fromkeys(reasons))+'; no paced allowance before deadline'
    else:
        reason = '; '.join(dict.fromkeys(reasons)) if reasons else 'Within time pace; at most one expensive action before recheck'
    return {'allowed':not reasons, 'reason':reason,
            'next_eligible_at':wake.isoformat() if wake else None,
            'windows':rows, 'tolerance_fraction':tolerance,
            'dispatch_policy':'One expensive action only; no concurrent image calls; wait >=300s before next live sample.'}


def sample(vendor):
    boot_id = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    boot_now = time.clock_gettime(time.CLOCK_BOOTTIME)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else None
    if cache and cache['vendor']==vendor and cache['boot_id']==boot_id:
        age = boot_now-cache['boot_time']
        if 0 <= age < 300:
            return cache, age, False
    attempt=CACHE.with_name('quota-last-attempt.json')
    if attempt.exists():
        previous=json.loads(attempt.read_text())
        gap=boot_now-previous.get('boot_time',0)
        if previous.get('boot_id')==boot_id and 0<=gap<300:
            raise ValueError('Recent quota poll failed/interrupted; five-minute retry cooldown is active')
    CACHE.parent.mkdir(exist_ok=True)
    attempt.write_text(json.dumps({'boot_id':boot_id,'boot_time':boot_now})+'\n')
    attempt.chmod(0o600)
    data = read_cli()
    provider = next((x for x in data if x['vendor']==vendor), None)
    if not provider:
        raise ValueError('Requested provider is absent from the quota CLI')
    if not provider.get('server_time') or not provider.get('fetched_at'):
        raise ValueError('Quota CLI did not expose trusted sample timestamps')
    raw = provider.get('raw') or {}
    allowed = (raw.get('rate_limit') or {}).get('allowed')
    if allowed is None:
        allowed = bool(provider.get('windows')) and not any(w.get('locked_reason') for w in provider['windows'])
    record = {'vendor':vendor, 'server_time':provider['server_time'],
              'fetched_at':provider['fetched_at'], 'provider_allowed':allowed,
              'windows':[{k:w.get(k) for k in ['kind','label','used','length','resets_at','started','locked_reason']} for w in provider['windows']],
              'boot_id':boot_id, 'boot_time':time.clock_gettime(time.CLOCK_BOOTTIME)}
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(record,indent=2)+'\n')
    CACHE.chmod(0o600)
    return record, 0., True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor',default='codex')
    parser.add_argument('--deadline',help='ISO8601 UTC; no expensive actions after this time')
    args = parser.parse_args()
    try:
        record, age, live = sample(args.vendor)
        now = timestamp(record['server_time'])+timedelta(seconds=age)
        fetched = timestamp(record['fetched_at'])
        if (now-fetched).total_seconds()>900:
            raise ValueError('Quota sample is older than 15 minutes')
        result = evaluate(record,now,timestamp(args.deadline) if args.deadline else None)
        result.update({'trusted_now':now.isoformat(), 'vendor':args.vendor,
                       'live_sample':live, 'sample_age_seconds':round(age,1)})
        print(json.dumps(result,indent=2))
    except Exception as error:
        print(json.dumps({'allowed':False,'reason':str(error),'next_eligible_at':None},indent=2))
        raise SystemExit(2)


if __name__=='__main__':
    main()
