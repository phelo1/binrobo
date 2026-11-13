#!/usr/bin/env python3
"""Rev G4 two-way audio API STUB for the bin-tug (owner app <-> tug, WebRTC audio over 4G).

What runs where (planned, not built):
  owner phone app  --HTTPS (signalling)-->  cloud relay (small VPS: this API + coturn TURN server)  <--outbound WSS--  tug (Pi Zero 2 W)
  media: Opus 16 kHz mono, ~24 kbit/s, DTLS-SRTP, relayed through TURN (the 4G modem is behind carrier-grade NAT, so the tug
  can never be dialled directly; it keeps one outbound WebSocket to the relay open while awake).
  Tug side media stack (planned): aiortc (Python WebRTC) or GStreamer webrtcbin, ALSA I2S devices (MEMS mic + class-D amp),
  PipeWire/PulseAudio module-echo-cancel (WebRTC AEC) because the speaker and mic sit 0.3 m apart on the mast.

This file is a STUB: the SDP 'answer' is canned and no audio flows. It defines the message formats and the state machine the
companion uses (companion.py: announce(), audio_tick()), and an aiohttp app with the REST endpoints so the app team can code
against it. Self-test:  python3 audio_api.py selftest
"""
import json, sys, time, uuid, asyncio

FAKE_OFFER = 'v=0\r\no=- 0 0 IN IP4 0.0.0.0\r\ns=-\r\nt=0 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\na=rtpmap:111 opus/48000/2\r\na=sendrecv\r\n'
CLIPS = {'vehicle': 'Bin robot stopped - please pass slowly', 'pinch': 'Please stand clear of the bin robot',
         'centre_gap': 'Please step away from behind the bin robot', 'hello': 'Hello - this is the bin robot'}
STATES = ('off', 'idle', 'announce', 'ringing', 'call')
ICE = [{'urls': 'stun:relay.example.invalid:3478'},
       {'urls': 'turn:relay.example.invalid:3478?transport=udp', 'username': '<ephemeral>', 'credential': '<hmac>'}]


class MockTug:
    """Tug-side audio controller stub (one call at a time, owner has priority over canned clips)."""
    def __init__(self):
        self.state = 'idle'; self.session = None; self.log = []; self.volume = 0.8; self.mic_muted = False

    def handle_offer(self, offer):
        if offer.get('type') != 'offer' or 'm=audio' not in offer.get('sdp', ''): raise ValueError('need an SDP offer with an audio m-line')
        if self.state in ('ringing', 'call'): raise RuntimeError('busy: a call is already ringing or active')
        sid = uuid.uuid4().hex[:8]; self.session = dict(id=sid, t0=time.time()); self.state = 'ringing'
        ans = offer['sdp'].replace('a=sendrecv', 'a=sendrecv\r\na=setup:active')        # canned (STUB)
        self.log.append(dict(kind='offer', session=sid))
        return dict(session_id=sid, type='answer', sdp=ans, codec='opus/16000/1 24kbit/s', ice_servers=ICE, stub=True)

    def connected(self): self.state = 'call'; self.log.append(dict(kind='connected', session=self.session['id']))

    def hangup(self, sid):
        if not self.session or self.session['id'] != sid: raise KeyError(sid)
        self.log.append(dict(kind='hangup', session=sid, dur_s=round(time.time() - self.session['t0'], 2))); self.session = None; self.state = 'idle'

    def announce(self, clip):
        if clip not in CLIPS: raise KeyError(clip)
        if self.state == 'call': return dict(played=False, why='owner call active')
        self.log.append(dict(kind='announce', clip=clip)); return dict(played=True, text=CLIPS[clip])

    def status(self): return dict(state=self.state, session=None if not self.session else self.session['id'], volume=self.volume, mic_muted=self.mic_muted)


def make_app(tug=None):
    from aiohttp import web
    tug = tug or MockTug(); app = web.Application(); app['tug'] = tug
    async def offer(req):
        try: return web.json_response(tug.handle_offer(await req.json()))
        except ValueError as e: return web.json_response(dict(error=str(e)), status=400)
        except RuntimeError as e: return web.json_response(dict(error=str(e)), status=409)
    async def ice(req):          # trickle ICE candidates from the app (stub: accepted and ignored)
        return web.json_response(dict(ok=True, session=req.match_info['sid']))
    async def connected(req): tug.connected(); return web.json_response(tug.status())
    async def hangup(req):
        try: tug.hangup(req.match_info['sid']); return web.json_response(tug.status())
        except KeyError: return web.json_response(dict(error='no such session'), status=404)
    async def announce(req):
        try: return web.json_response(tug.announce((await req.json())['clip']))
        except KeyError: return web.json_response(dict(error='unknown clip', clips=list(CLIPS)), status=400)
    async def status(req): return web.json_response(tug.status())
    async def volume(req):
        b = await req.json(); tug.volume = float(min(1, max(0, b.get('volume', tug.volume)))); tug.mic_muted = bool(b.get('mic_muted', tug.mic_muted))
        return web.json_response(tug.status())
    app.router.add_post('/api/v1/audio/session', offer)
    app.router.add_post('/api/v1/audio/session/{sid}/ice', ice)
    app.router.add_post('/api/v1/audio/session/{sid}/connected', connected)
    app.router.add_delete('/api/v1/audio/session/{sid}', hangup)
    app.router.add_post('/api/v1/audio/announce', announce)
    app.router.add_get('/api/v1/audio/state', status)
    app.router.add_post('/api/v1/audio/settings', volume)
    return app


async def _selftest():
    from aiohttp.test_utils import TestServer, TestClient
    app = make_app(); out = []
    async with TestClient(TestServer(app)) as c:
        async def call(m, u, **kw):
            r = await getattr(c, m)(u, **kw); j = await r.json(); out.append('%s %s -> %d %s' % (m.upper(), u, r.status, json.dumps(j)[:110])); return r.status, j
        await call('get', '/api/v1/audio/state')
        await call('post', '/api/v1/audio/announce', json=dict(clip='vehicle'))
        st, j = await call('post', '/api/v1/audio/session', json=dict(type='offer', sdp=FAKE_OFFER)); sid = j['session_id']
        await call('post', '/api/v1/audio/session', json=dict(type='offer', sdp=FAKE_OFFER))          # 409: already ringing
        await call('post', '/api/v1/audio/session/%s/ice' % sid, json=dict(candidate='candidate:1 1 udp 2122260223 10.0.0.2 50000 typ host'))
        await call('post', '/api/v1/audio/session/%s/connected' % sid)
        await call('post', '/api/v1/audio/session', json=dict(type='offer', sdp=FAKE_OFFER))          # 409 busy
        await call('post', '/api/v1/audio/announce', json=dict(clip='pinch'))                            # suppressed during the call
        await call('delete', '/api/v1/audio/session/%s' % sid)
        await call('post', '/api/v1/audio/session', json=dict(type='offer', sdp='v=0'))                 # 400
        await call('post', '/api/v1/audio/announce', json=dict(clip='nope'))                            # 400
    return out

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'selftest':
    for l in asyncio.run(_selftest()): print(l)
