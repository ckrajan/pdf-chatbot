var pdf_list;
var datalist = document.getElementById("pdfInput");

get_uploaded_files()
  .then(console.log("Ententia"))
  .catch((error) => console.error("error", error));

function get_populated_list() {
  var t = JSON.parse(pdf_list);
  return t;
}

function populateList(arr) {
  arr.forEach((pdf) => {
    var option = document.createElement("option");
    option.innerHTML = pdf;
    datalist.appendChild(option);
  });
}

async function get_uploaded_files() {
  const { request } = await axios.post("/uploaded_files", {
    contentType: "text/json",
  });
  pdf_list = request.responseText;
  populateList(get_populated_list());
  return request;
}

async function get_response() {
  document.getElementById("loader").style.display = "block";
  const { request } = await axios.post("/get_response", {
    prompt: $("#query").val(),
    contentType: "text/json",
  });

  $("#answer").val(request.responseText);
  document.getElementById("loader").style.display = "none";
}
