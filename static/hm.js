$(function () {
    $("#id_sector").on("change", function () {
      if (this.value === "Other") {
        $("#id_other_sector").prop("required", function () {
          return true;
        });
        $("#other_sector").removeClass("d-none");
        console.log(this.value);
      }
      if (this.value !== "Other") {
        $("#other_sector").addClass("d-none");
        $("#id_other_sector").prop("required", function () {
          return false;
        });
      }
    });
  });