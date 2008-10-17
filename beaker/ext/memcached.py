from beaker.container import NamespaceManager, Container
from beaker.exceptions import InvalidCacheBackendError, MissingCacheParameter
from beaker.synchronization import file_synchronizer, null_synchronizer
from beaker.util import verify_directory, SyncDict

try:
    import cmemcache as memcache
except ImportError:
    try:
        import memcache
    except ImportError:
        raise InvalidCacheBackendError("Memcached cache backend requires either the 'memcache' or 'cmemcache' library")

class MemcachedNamespaceManager(NamespaceManager):
    clients = SyncDict()
    
    def __init__(self, namespace, url, data_dir=None, lock_dir=None, **params):
        NamespaceManager.__init__(self, namespace)
        
        if lock_dir is not None:
            self.lock_dir = lock_dir
        elif data_dir is None:
            raise MissingCacheParameter("data_dir or lock_dir is required")
        else:
            self.lock_dir = data_dir + "/container_mcd_lock"
        
        verify_directory(self.lock_dir)            
        
        self.mc = MemcachedNamespaceManager.clients.get(url, 
            memcache.Client, url.split(';'), debug=0)

    def get_access_lock(self):
        return null_synchronizer()

    def get_creation_lock(self, key):
        return file_synchronizer(
            identifier="memcachedcontainer/funclock/%s" % self.namespace,lock_dir = self.lock_dir)

    def open(self, *args, **params):
        pass
        
    def close(self, *args, **params):
        pass

    def _format_key(self, key):
        return self.namespace + '_' + key.replace(' ', '\302\267')

    def __getitem__(self, key):
        return self.mc.get(self._format_key(key))

    def __contains__(self, key):
        value = self.mc.get(self._format_key(key))
        return value is not None

    def has_key(self, key):
        return key in self

    def set_value(self, key, value, expiretime=None):
        if expiretime:
            self.mc.set(self._format_key(key), value, time=expiretime)
        else:
            self.mc.set(self._format_key(key), value)

    def __setitem__(self, key, value):
        self.set_value(key, value)
        
    def __delitem__(self, key):
        self.mc.delete(self._format_key(key))

    def do_remove(self):
        self.mc.flush_all()
    
    def keys(self):
        raise NotImplementedError("Memcache caching does not support iteration of all cache keys")

class MemcachedContainer(Container):
    namespace_class = MemcachedNamespaceManager
