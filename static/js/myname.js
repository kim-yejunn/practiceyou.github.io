function setMobileVh() {
    let mobileVh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${mobileVh}px`);
  }