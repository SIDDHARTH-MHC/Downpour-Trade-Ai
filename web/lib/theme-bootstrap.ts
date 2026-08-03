export function themeBootstrapScript() {
  return `(function(){try{var t=localStorage.getItem("downpour.theme")||"dark";var d=localStorage.getItem("downpour.density")||"comfortable";var w=localStorage.getItem("downpour.workspace")||"trading";var r=t==="light"?"light":t==="dark"?"dark":window.matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";document.documentElement.classList.add(r);document.documentElement.dataset.density=d;document.documentElement.dataset.workspace=w;}catch(e){document.documentElement.classList.add("dark");}})();`;
}
