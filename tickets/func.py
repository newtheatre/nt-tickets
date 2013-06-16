import os
import hashlib
def rand_16():
	random_data = os.urandom(128)
	return hashlib.md5(random_data).hexdigest()[:16]