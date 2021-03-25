$(function() {
    function showBtnNext() {
        if (($('#passport').children().length >= 1) && ($('#edu').children().length >= 1) && ($('#edu_inside').children().length >= 1)) {
            $('#btnNext').show();
        }
        else {
            $('#btnNext').hide();
        }
    }

    function loadDocs(data, doctype) {
        if (doctype == 1) {
            $('#passport').append(data);
        } else if (doctype == 2) {
            $('#edu').append(data);
        } else if (doctype == 3) {
            $('#achievement').append(data);
        } else if (doctype == 4) {
            $('#other').append(data);
        } else if (doctype == 5) {
            $('#photo').append(data);
        } else if (doctype == 20) {
            $('#edu_inside').append(data);
        }
        $('.cssload-loader').hide();
        showBtnNext();
    }

    function loadDocuments(doctype) {
        $('#openDialog').click();
        $('#openDialog').off('change').on('change', function () {
            var docs = this.files;
            if (docs.length > 0) {
                $('.cssload-loader').show();
                var data = new FormData();
                data.append("doctype", doctype);
                $.each( docs, function(key, value) {
                    data.append(key, value);
                });
                jQuery.ajax({
                    type: "POST",
                    url: load_link,
                    data: data,
                    cache: false,
                    processData: false,
                    contentType: false,
                    success: function(data){loadDocs(data, doctype);},
                    error: function(data){
                        $('.cssload-loader').hide();
                    }
                });
            }
        });
    }

    $('#btnOne,#btnTwo,#btnThree,#btnFour,#btnFive,#btnSix').on('click', function() {
        loadDocuments($(this).data("doctype"));
    });

    showBtnNext();
});