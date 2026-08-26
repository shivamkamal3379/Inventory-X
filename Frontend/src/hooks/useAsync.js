import { useCallback, useEffect, useRef, useState } from 'react';
import { errorMessage } from '../services/apiClient';

/**
 * Runs an async loader and tracks {data, loading, error}.
 *
 * Guards against setting state after unmount, and ignores the response of a
 * superseded call — without that, a slow search for "dr" can land after a
 * faster one for "drill" and overwrite the newer results.
 */
export function useAsync(loader, deps = [], { immediate = true } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const mounted = useRef(true);
  const callId = useRef(0);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const run = useCallback(async () => {
    const id = ++callId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      if (mounted.current && id === callId.current) setData(result);
      return result;
    } catch (err) {
      if (mounted.current && id === callId.current) setError(errorMessage(err));
      return undefined;
    } finally {
      if (mounted.current && id === callId.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    if (immediate) run();
  }, [run, immediate]);

  return { data, loading, error, reload: run, setData };
}

/** Delays a fast-changing value, so typing does not fire a request per keystroke. */
export function useDebounced(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}
