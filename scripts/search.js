function searchKeyDown(event) {
  if (event.key === "Enter") {
    searchButtonClick();
    document.getElementById("search_button").click();    }
}


function searchButtonClick() {
  const search_value = document.getElementById("search_box").value;
  let search_url;
  let base_url;

  const current_href = window.location.href;

  if (current_href.includes("evykassirer.github.io")) {
    base_url = "https://evykassirer.github.io/tools-of-change";
  } else {
    base_url = window.location.origin;
  }

  if (current_href.includes("/en/")) {
    search_url = base_url + "/en/search";
  } else {
    search_url = base_url + "/fr/recherche";
  }

  params = new URLSearchParams();
  if (search_value) {
    params.append("query", search_value);
  }

  if (current_href.includes("en/case-studies") || current_href.includes("fr/etudes-de-cas")) {
      params.append("type", "case-study");
  }

  // NOTE: french topic resources don't currently have the box set up for them
  // but I can probably add it by it being part of the path?
  if (current_href.includes("en/topic-resources") || current_href.includes("fr/ressources-de-sujets")) {
      params.append("type", "topic-resource");
  }

  if (params.size > 0) {
    search_url = search_url + "?" + params.toString();
  }

  window.location.href = search_url;
};
