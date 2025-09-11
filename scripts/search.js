function searchKeyDown(event) {
  if (event.key === "Enter") {
    searchButtonClick();
    document.getElementById("search_button").click();    }
}


function searchButtonClick() {
  const search_value = document.getElementById("search_box").value;
  let search_url;
  if (window.location.href.includes("/en/")) {
    search_url = "../../en/search?query=";
  } else {
    search_url = "../../fr/recherche?query=";
  }
  if (search_value) {
    window.location.href = search_url + search_value;
  }
};
