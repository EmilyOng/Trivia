var questions = JSON.parse({{questions|tojson}});
var answers = JSON.parse({{answers|tojson}});
var globalQuestionPanel = document.getElementById("globalQuestionPanel");
var button = document.getElementById("startGlobalButton");

window.addEventListener("DOMContentLoaded", (event) => {
    // Check game state
    var askedQuestions = localStorage.getItem("Trivia_Asked");
    if (askedQuestions != null) {
      button.style.display = "none";
      showQuestion();
    }
});

function showQuestion () {
  var questionID = JSON.parse(localStorage.getItem("Trivia_ID"));
  var askedQuestions = JSON.parse(localStorage.getItem("Trivia_Asked"));
  var questions = JSON.parse(localStorage.getItem("Trivia_Questions"));
  var size = questionID.length;
  var chosenQuestion;
  if (askedQuestions.length < size) {
    while (true) {
      var randIndex = Math.floor(Math.random() * size);
      var found = false;
      for (var i = 0; i < askedQuestions.length; i ++) {
        if (askedQuestions[i] == questionID[randIndex]) {
          found = true;
          break;
        }
      }
      if (!found) {
        askedQuestions.push(questionID[randIndex]);
        chosenQuestion = questionID[randIndex];
        localStorage.setItem("Trivia_Asked", JSON.stringify(askedQuestions));
        break;
      }
    }
    var template = '<div class="card border-dark">\
                    <div class="card-header cardTitle"></div>\
                    <div class="card-body text-dark">\
                    <p class="card-text cardText"></p>\
                    </div>\
                    </div>';
    globalQuestionPanel.innerHTML = template;
    var question = questions[chosenQuestion];
    var cardTitle = document.getElementsByClassName("cardTitle");
    cardTitle = cardTitle[cardTitle.length - 1];
    cardTitle.appendChild(document.createTextNode(question["questionText"]));

    var form = document.createElement("form");
    form.setAttribute("method", "POST");
    form.setAttribute("action", "/submitAnswers");
    var optionForm = '<div class="form-check gameOption">\
                      <input class="form-check-input" type="radio" required>\
                      <label class="form-check-label"></label>\
                      </div>'

    var cardText = document.getElementsByClassName("cardText");
    cardText = cardText[cardText.length - 1];
    cardText.appendChild(form);

    var options = question["options"];
    for (var i = 0; i < options.length; i ++ ) {
      var option = options[i];
      if (option.length > 0) {
        form.innerHTML += optionForm;
        var gameOption = document.getElementsByClassName("gameOption");
        gameOption = gameOption[gameOption.length - 1];
        gameOption.children[0].setAttribute("name", chosenQuestion);
        gameOption.children[0].setAttribute("value", option);
        gameOption.children[0].setAttribute("class", "question_"+chosenQuestion);
        gameOption.children[0].setAttribute("id", "question"+String(i+1)+"_"+chosenQuestion);
        gameOption.children[0].setAttribute("onchange", "selectOption(this)");
        gameOption.children[1].setAttribute("for", "question_"+String(i+1)+"_"+chosenQuestion);
        gameOption.children[1].appendChild(document.createTextNode(option))
      }
    }
    form.innerHTML += "<br/><button type='type' onclick='showAnswer(this); event.preventDefault();' class='btn btn-warning checkAnswerButton'>Check Answer</button><br/>";
    var msg = '<br/><div class="alert alert-dismissible fade show col-4 questionMessage" role="alert"></div>';
    form.innerHTML += msg;
    var msgs = document.getElementsByClassName("questionMessage");
    msgs[msgs.length - 1]. setAttribute("id", "msg_"+chosenQuestion);
    form.innerHTML += "<br/><button type='submit'style='display:none;' class='btn btn-success checkAnswerButton'>Next</button>";
    var checkAnswerButtons = document.getElementsByClassName("checkAnswerButton");
    var index = checkAnswerButtons.length;
    checkAnswerButtons[index - 2].setAttribute("id", "check_"+chosenQuestion);
    checkAnswerButtons[index - 1].setAttribute("id", "submit_"+chosenQuestion);
  }
  else {
    // Out of questions
  }
}

function selectOption (select_) {
  var id_components = select_.id.split("_")
  var id = id_components[1];
  document.getElementById("check_"+id).setAttribute("value", select_.value);
}

function showAnswer (btn) {
  var id_components = btn.id.split("_")
  var id = id_components[1];
  // Check answer for question id
  var given_answer = btn.value;
  var correct_answer = answers[id];
  var color, msg;
  if (given_answer == correct_answer) {
    color = "alert-success";
    msg = "Congratuations, you have given the right answer!";
  }
  else {
    color = "alert-danger";
    msg = "That is unfortunately not the right answer!";
  }
  var button = '<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
                  <span aria-hidden="true">&times;</span>\
                </button>';
  $("#msg_"+id).addClass(color);
  document.getElementById("msg_"+id).appendChild(document.createTextNode(msg));
  document.getElementById("msg_"+id).innerHTML += button;
  var options = document.getElementsByClassName("question_"+id);
  for (var i = 0; i < options.length; i ++) {
    options[i].setAttribute("disabled", true);
  }
  btn.style.display = "none";
  document.getElementById("submit_"+id).style.display = "block";
}

function startGame () {
  button.style.display = "none";
  if (button.value == "Start") {
    localStorage.setItem("Trivia_Questions", JSON.stringify(questions));
    localStorage.setItem("Trivia_Asked", JSON.stringify([]));
    var questionID = [];
    for (var question in questions) { questionID.push(question); }
    localStorage.setItem("Trivia_ID", JSON.stringify(questionID));
  }
  showQuestion();
}
