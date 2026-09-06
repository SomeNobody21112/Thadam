import { useEffect, useRef, useState } from "react";

const REDUCED = () =>
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/**
 * Reveal an element when it scrolls into view.
 * Returns [ref, isVisible]. Attach ref to the element and use `reveal` classes.
 */
export function useReveal({ threshold = 0.12, once = true, rootMargin = "0px 0px -8% 0px" } = {}) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (REDUCED()) {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          if (once) observer.unobserve(node);
        } else if (!once) {
          setVisible(false);
        }
      },
      { threshold, rootMargin }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [threshold, once, rootMargin]);

  return [ref, visible];
}

/**
 * Count from 0 up to `end` once `active` turns true. Eased, frame-based.
 *
 * Browsers do not run `requestAnimationFrame` in a background tab. If the page
 * loaded hidden — which is exactly what happens when you open the demo in a tab
 * and switch to it a moment later — the first frame never arrived, the `started`
 * latch was already set, and the figure stayed on 0 permanently, even once the
 * tab was focused. So: while hidden, skip straight to the final value, and only
 * animate when there is actually a compositor to animate for.
 */
export function useCountUp(end, { duration = 1500, active = true, decimals = 0 } = {}) {
  const [value, setValue] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    if (started.current || end == null) return;

    // Every path lands on the same rounding, so a counter that skips the
    // animation reads identically to one that ran it.
    const quantise = (v) => (decimals ? Number(v.toFixed(decimals)) : Math.round(v));

    // A hidden document has no compositor: requestAnimationFrame will not tick,
    // and the IntersectionObserver driving `active` may never report either. Land
    // on the real figure rather than waiting for frames that are not coming.
    if (REDUCED() || document.hidden) {
      started.current = true;
      setValue(quantise(end));
      return;
    }
    if (!active) return;

    started.current = true;
    let raf;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / duration);
      // easeOutExpo — fast start, gentle landing
      const eased = p === 1 ? 1 : 1 - Math.pow(2, -10 * p);
      setValue(quantise(end * eased));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    // If the tab is backgrounded mid-count the frames stop; land on the real
    // figure rather than freezing part-way there.
    const onHide = () => { if (document.hidden) { cancelAnimationFrame(raf); setValue(quantise(end)); } };
    document.addEventListener("visibilitychange", onHide);
    return () => {
      cancelAnimationFrame(raf);
      document.removeEventListener("visibilitychange", onHide);
    };
  }, [end, duration, active, decimals]);

  return value;
}

/** Current scroll position in pixels, throttled to animation frames. */
export function useScrollY() {
  const [y, setY] = useState(0);
  useEffect(() => {
    let raf = null;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        setY(window.scrollY);
        raf = null;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);
  return y;
}

/** 0 -> 1 progress through the whole document. Drives the top progress bar. */
export function useScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    let raf = null;
    const update = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const max = document.body.scrollHeight - window.innerHeight;
        setProgress(max > 0 ? Math.min(1, window.scrollY / max) : 0);
        raf = null;
      });
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);
  return progress;
}

/** Track the cursor inside an element, as 0..1 coordinates, for spotlight effects. */
export function usePointerSpotlight() {
  const ref = useRef(null);
  useEffect(() => {
    const node = ref.current;
    if (!node || REDUCED()) return;
    const onMove = (e) => {
      const rect = node.getBoundingClientRect();
      node.style.setProperty("--mx", `${((e.clientX - rect.left) / rect.width) * 100}%`);
      node.style.setProperty("--my", `${((e.clientY - rect.top) / rect.height) * 100}%`);
    };
    node.addEventListener("pointermove", onMove);
    return () => node.removeEventListener("pointermove", onMove);
  }, []);
  return ref;
}

/**
 * Hold a value still until it has stopped changing for `delay` milliseconds.
 *
 * The audit-plan and rota sliders each drive a request that recomputes a plan. Firing on
 * every `onChange` meant a drag from 5 to 250 days queued roughly fifty requests, and the
 * screen sat on whichever one happened to land last — which is why the page appeared to
 * hang while the number under the slider had long since settled.
 *
 * The displayed number still tracks the slider exactly. Only the fetch waits.
 */
export function useDebounced(value, delay = 320) {
  const [settled, setSettled] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setSettled(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return settled;
}
