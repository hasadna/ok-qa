{% load i18n qa_tags %}

{% with QUESTION_ID="000000000" %} {# placeholder for url #}

var voteAjaxError = function (evt, jqXHR, setting, err) {
    $("#messages").html('<div class="alert" class="error">' +
            '<button type="button" class="close" data-dismiss="alert">×</button>' +
            jqXHR.responseText + '</div>');
};

$(".upvote-question").ajaxError(voteAjaxError);
$(".downvote-question").ajaxError(voteAjaxError);

$(".upvote-question").click(function () {
    {% if not question|can_vote:user %}
        $("#messages").html('<div class="alert" class="info">' +
                '<button type="button" class="close" data-dismiss="alert">×</button>' +
                "{% trans 'Sorry but only connected users can upvote questions' %}" +
                '</div>');
    {% else %}
        var qid = $(this).closest('.question-summary').attr('question-id');
        $.post("{% url 'upvote_question' QUESTION_ID %}"
                .replace("{{ QUESTION_ID }}", qid),
                {csrfmiddlewaretoken: "{{ csrf_token }}"},
                function (data, status, jqXHR) {
                    $("#votes-count-" + qid).html(jqXHR.responseText);
                    $(".votes-" + qid).css("visibility", "visible");
                    $("#upvote-question-" + qid).hide();
                    $("#downvote-question-" + qid).show();
                });
    {% endif %}
    return false;
});

$(".downvote-question").click(function () {
    var qid = $(this).closest('.question-summary').attr('question-id');
    $.post("{% url 'downvote_question' QUESTION_ID %}"
            .replace("{{ QUESTION_ID }}", qid),
           {csrfmiddlewaretoken: "{{ csrf_token }}"},
           function (data, status, jqXHR) {
             $("#votes-count-" + qid).html(jqXHR.responseText);
             $(".votes-" + qid).css("visibility", "visible");
             $("#upvote-question-" + qid).show();
             $("#downvote-question-" + qid).hide();
           });
    return false;
});


$(".flag-question").click(function (e) {
    var qid = $(this).closest('.question-summary').attr('question-id');
    var url = "{% url 'flag_question' QUESTION_ID %}"
              .replace("{{ QUESTION_ID }}", qid);
    {% if user == question.author %}
    if (!confirm("{% trans 'Are you sure you want to delete the question?' %}")) {
      return;
    }
    {% endif %}
    $.post(url, {csrfmiddlewaretoken: "{{ csrf_token }}"})
        .done(function (data, textStatus, jqXHR) {
          window.location.replace(data);
        });
  })

{% endwith %}
