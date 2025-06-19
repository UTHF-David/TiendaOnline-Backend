import ably
from ably import AblyRest
import os

ABLY_API_KEY = os.getenv('ABLY_API_KEY', 'qZLZMg.GvMK6Q:qaQcoQyJSX2q7Gl4TFi-HV2Vj1NMnjltCM4e_JoUJgc')

ably_client = AblyRest(ABLY_API_KEY)