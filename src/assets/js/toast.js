$(function () {
    let borderColor, bodyBg, headingColor;
  
    if (isDarkStyle) {
      borderColor = config.colors_dark.borderColor;
      bodyBg = config.colors_dark.bodyBg;
      headingColor = config.colors_dark.headingColor;
    } else {
      borderColor = config.colors.borderColor;
      bodyBg = config.colors.bodyBg;
      headingColor = config.colors.headingColor;
    }
    var toastElements = document.querySelectorAll('.toast');
  
    if (toastElements) {
      toastElements.forEach(function (element) {
        var toast = new bootstrap.Toast(element);
        toast.show();
      });
    }
  });
