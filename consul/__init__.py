__version__ = "1.5.5"

from consul.check import Check
from consul.exceptions import ACLDisabled, ACLPermissionDenied, ConsulException, NotFound, Timeout
from consul.std import Consul
