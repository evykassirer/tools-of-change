function searchKeyDown(event) {
  if (event.key === "Enter") {
    searchButtonClick();
    document.getElementById("search_button").click();    }
}


function searchButtonClick() {
  const search_value = document.getElementById("search_box").value;
  if (search_value) {
    window.location.href = "../../search_playground.html?query=" + search_value;
  }
};
