import { useState, useEffect, useSyncExternalStore } from 'react';
import { flush, subscribe, queueSize } from '../lib/offlineQueue';

/** Announcement bar — ink background, white mono text, 40px tall.
 *  Drains the offline queue when connectivity returns. */
export default function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine);
  const [syncing, setSyncing] = useState(false);
  const size = useSyncExternalStore(subscribe, queueSize);

  useEffect(() => {
    const goOn = async () => {
      setOffline(false);
      if (queueSize() > 0) {
        setSyncing(true);
        await flush();
        setSyncing(false);
      }
    };
    const goOff = () => setOffline(true);
    window.addEventListener('offline', goOff);
    window.addEventListener('online', goOn);
    return () => {
      window.removeEventListener('offline', goOff);
      window.removeEventListener('online', goOn);
    };
  }, []);

  if (!offline && size === 0 && !syncing) return null;

  let message = "You're offline — changes will sync when reconnected";
  if (syncing) message = `Syncing ${size} pending change${size === 1 ? '' : 's'}…`;
  else if (!offline && size > 0) message = `${size} change${size === 1 ? '' : 's'} waiting to sync`;

  return (
    <div className="no-select fixed top-0 left-0 right-0 z-[100] flex h-10 items-center justify-center bg-ink px-4" style={{ paddingTop: 'env(safe-area-inset-top, 0px)' }}>
      <p className="font-mono text-body-sm text-parchment uppercase tracking-body-sm truncate">
        {message}
      </p>
    </div>
  );
}
