var pdf_list;
var datalist = document.getElementById("pdfInput");
var answerBtn = document.getElementById("click_answer");
var removeFile = document.getElementById("remove_file");

get_uploaded_files()
  .then(console.log("Ententia"))
  .catch((error) => console.error("error", error));

function get_populated_list() {
  var t = JSON.parse(pdf_list);
  if(t.length == 0){
    answerBtn.style.display = "none";
    removeFile.style.display = "none";
  }
  else {
    answerBtn.style.display = "inline";
    removeFile.style.display = "inline";
  }
  return t;
}

function populateList(arr) {
  if(arr.length != 0){
    arr.forEach((pdf) => {
      var option = document.createElement("option");
      option.innerHTML = pdf;
      datalist.appendChild(option);
    });
  }
  else {
    $("#pdfInput").empty();
  }
}

async function get_uploaded_files() {
  const { request } = await axios.post("/uploaded_files", {
    contentType: "text/json",
  });
  pdf_list = request.responseText;
  populateList(get_populated_list());
  return request;
}

async function remove_file() {
  const { request } = await axios.post("/remove_file", {
    contentType: "text/json",
  });
  get_uploaded_files()
  .then(console.log("Ententia"))
  .catch((error) => console.error("error", error));
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
