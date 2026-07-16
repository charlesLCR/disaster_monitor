(() => {
  const ANGLES = [0, 60, 120, 180, 240, 300];

  const currentAngleEl = document.getElementById("current-angle");
  const dialAngleEl = document.getElementById("dial-angle");
  const dialNeedle = document.getElementById("dial-needle");
  const feedbackEl = document.getElementById("feedback");
  const angleButtons = Array.from(document.querySelectorAll(".angle-btn"));
  const btnLeft = document.getElementById("btn-left");
  const btnRight = document.getElementById("btn-right");
  const btnHome = document.getElementById("btn-home");

  let currentAngle = 0;
  let busy = false;

  function setFeedback(text, state = "") {
    feedbackEl.textContent = text;
    feedbackEl.classList.remove("is-busy", "is-done");
    if (state) feedbackEl.classList.add(state);
  }

  function setControlsEnabled(enabled) {
    [...angleButtons, btnLeft, btnRight, btnHome].forEach((btn) => {
      btn.disabled = !enabled;
    });
  }

  function syncActiveButton(angle) {
    angleButtons.forEach((btn) => {
      btn.classList.toggle("is-active", Number(btn.dataset.angle) === angle);
    });
  }

  function updateReadout(angle) {
    currentAngleEl.textContent = String(angle);
    dialAngleEl.textContent = `${angle}°`;
    dialNeedle.style.transform = `rotate(${angle}deg)`;
    syncActiveButton(angle);
  }

  async function rotateTo(targetAngle) {
    if (busy) return;
    if (!ANGLES.includes(targetAngle)) return;
    if (targetAngle === currentAngle) {
      setFeedback(`已在 ${targetAngle}°，无需转动`, "is-done");
      return;
    }

    busy = true;
    setControlsEnabled(false);
    setFeedback(`正在转向 ${targetAngle}° …`, "is-busy");

    try {
      const res = await fetch("/api/motor/rotate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ angle: targetAngle }),
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok || !data.ok) {
        throw new Error(data.error || `请求失败 (${res.status})`);
      }

      currentAngle = Number(data.angle);
      updateReadout(currentAngle);
      setFeedback(`已到位 · 当前方位 ${currentAngle}°`, "is-done");
    } catch (err) {
      setFeedback(`转向失败：${err.message || err}`, "is-busy");
    } finally {
      setControlsEnabled(true);
      busy = false;
    }
  }

  function stepBy(delta) {
    const idx = ANGLES.indexOf(currentAngle);
    const safeIdx = idx >= 0 ? idx : 0;
    const next = ANGLES[(safeIdx + delta + ANGLES.length) % ANGLES.length];
    rotateTo(next);
  }

  async function syncStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      if (res.ok && data.ok && data.current_angle != null) {
        currentAngle = Number(data.current_angle);
        updateReadout(currentAngle);
        setFeedback(`已连接 · 当前方位 ${currentAngle}°`, "is-done");
      }
    } catch (_) {
      setFeedback("无法连接服务，请通过 Flask 打开本页", "is-busy");
    }
  }

  angleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      rotateTo(Number(btn.dataset.angle));
    });
  });

  btnLeft.addEventListener("click", () => stepBy(-1));
  btnRight.addEventListener("click", () => stepBy(1));
  btnHome.addEventListener("click", () => rotateTo(0));

  updateReadout(currentAngle);
  syncStatus();
})();
