document.getElementById("addToGlobal").onclick = function () {
  if (document.getElementById("addToGlobalForm").style.display == "none") {
    document.getElementById("addToGlobalForm").style.display = "block";
  }
  else {
    document.getElementById("addToGlobalForm").style.display = "none";
  }
}
document.getElementById("addOption").onclick = function () {
  if (document.getElementById("options").childElementCount < 3) {
    var numOptions = String(document.getElementById("options").childElementCount + 1);
    var id = "optionText" + numOptions;
    var placeholder = "Enter Option " + numOptions;

    var newInput = document.createElement("div");
    newInput.setAttribute("class", "form-group col-4 justify-content-center form-inline")

    // LABEL //
    var label = document.createElement("label");
    label.setAttribute("for", id); // Assign label attribute
    label.appendChild(document.createTextNode(placeholder));
    label.append(document.createTextNode("\u00A0"));

    var deleteButton = document.createElement("button");
    deleteButton.setAttribute("class", "deleteButtons btn btn-danger");
    deleteButton.setAttribute("type", "button");
    deleteButton.setAttribute("id", "deleteOption"+numOptions); // Assign id to delete button
    deleteButton.setAttribute("onclick", "deleteOption(this)"); // Assign onclick action to delete button
    deleteButton.appendChild(document.createTextNode("\u2573"));

    deleteButton.text = "&cross;";
    label.appendChild(deleteButton);
    newInput.appendChild(label)

    newInput.appendChild(document.createTextNode("\u00A0"))

    // INPUT //
    var input = document.createElement("input");
    input.setAttribute("id", id); // Assign input id
    input.setAttribute("name", id); // Assign input name
    input.required = true;
    newInput.appendChild(input);

    document.getElementById("options").appendChild(newInput);

    // ANSWER //
    var answerOption = document.createElement("option");
    answerOption.appendChild(document.createTextNode(numOptions));
    document.getElementById("answer").appendChild(answerOption);
  }

}

function deleteOption (option) {
  var id = option.id;
  // const ID = id;
  var currID = parseInt(id.slice(12, id.length));
  var deleteButtons = document.getElementsByClassName("deleteButtons");
  var deleteElem = option.parentNode.parentNode;
  deleteElem.parentNode.removeChild(deleteElem);

  var answerOptions = document.getElementById("answer").children;

  answerOptions[currID - 1].parentNode.removeChild(answerOptions[currID - 1]);

  for (var i = 0; i < deleteButtons.length; i ++ ) {
    currID = parseInt(deleteButtons[i].id.slice(12, deleteButtons[i].id.length));
    if (currID != i+1) {
      var newID = String(i+1);

      answerOptions[i].innerHTML = newID;

      deleteButtons[i].setAttribute("id", "deleteOption"+newID);
      var addedOption = deleteButtons[i].parentNode.parentNode; // Assign id to delete button
      var pos = addedOption.children[0].innerHTML.search("&nbsp");
      var lengthHTML = addedOption.children[0].innerHTML.length;
      var chunk = addedOption.children[0].innerHTML.slice(pos, lengthHTML);
      var label = addedOption.children[0].innerHTML.slice(0, pos - 1);
      label = label + newID;
      addedOption.children[0].innerHTML = label + chunk;
      addedOption.children[0].setAttribute("for", "optionText"+newID); // Assign label attribute
      addedOption.children[1].setAttribute("id", "optionText"+newID); // Assign input id
      addedOption.children[1].setAttribute("name", "optionText"+newID); // Assign input name
    }
  }

}
