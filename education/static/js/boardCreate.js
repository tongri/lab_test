$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-board .modal-content").html("");
        $("#modal-board").modal("show");
      },
      success: function (data) {
        $("#modal-board .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#board-table tbody").html(data.html_book_list);
          $("#modal-board").modal("hide");
        }
        else {
          $("#modal-board .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // Create book
  $(".js-create-board").click(loadForm);
  $("#modal-board").on("submit", ".js-board-create-form", saveForm);

  // Update book
  $("#board-table").on("click", ".js-update-board", loadForm);
  $("#modal-board").on("submit", ".js-board-update-form", saveForm);

  // Delete book
  $("#board-table").on("click", ".js-delete-board", loadForm);
  $("#modal-board").on("submit", ".js-board-delete-form", saveForm);

});