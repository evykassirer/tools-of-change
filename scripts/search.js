function searchKeyDown(event) {
  if (event.key === "Enter") {
    searchButtonClick();
    document.getElementById("search_button").click();    }
}


function searchButtonClick() {
  const search_value = document.getElementById("search_box").value;
  let search_url;
  let base_url;
  if (window.location.href.includes("evykassirer.github.io")) {
    base_url = "https://evykassirer.github.io/tools-of-change";
  } else {
    base_url = window.location.origin;
  }

  if (window.location.href.includes("/en/")) {
    search_url = base_url + "/en/search?query=";
  } else {
    search_url = base_url + "/fr/recherche?query=";
  }
  if (search_value) {
    window.location.href = search_url + search_value;
  }
};
