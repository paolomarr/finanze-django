var processErrors = function(errors) {
    errors.forEach(element => {
        errel = $(`<div class="alert alert-damger" role="alert">${element}</div>`);
        $("#errors").append(errel);
    });
};
var clearErrors = () => {
    $("#errors").empty();
}
$(function(){
    var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    $('.category-select').click(event => {
        var checked = $(event.target).prop('checked');
        var category = $(event.target).val();
        data = {
            csrfmiddlewaretoken: csrftoken, 
            category: category, 
            checked: checked
        };
        $.ajax({url: "/movimenti/categories",
            method: "POST",
            data: data,
            success: function(response) {
                console.log("Update saved");
                console.log(JSON.stringify(response));
            },
            error: function(xhr, status, error) {
                console.log("Update failed");
            }
        });
    });
    $("#categoryDirectionSwitch").change(event => {
        var isIncoming = $(event.target).prop('checked');
        if(isIncoming){
            $(event.target).siblings('label')
                .removeClass('text-black-50')
                .addClass('fw-bolder')
                .addClass('text-primary');
        }else{
            $(event.target).siblings('label')
                .addClass('text-black-50')
                .removeClass('fw-bolder')
                .removeClass('text-primary');
        }
    });
    document.getElementsByName('category')[0].addEventListener("keyup", (event) => {
        var button = document.getElementById("createCategoryButton");
        if(event.target.value.length > 0){
            button.classList.remove('disabled');
        }else{
            button.classList.add('disabled');
        }
    });
    $('#createCategoryButton').click(event => {
        clearErrors();
        $(event.target).find('span').removeClass('d-none');
        var url = "/movimenti/categories/new";
        var catname = document.getElementsByName('category')[0].value;
        var isIncoming = $("#categoryDirectionSwitch").prop('checked');
        var direction = -1;
        if(isIncoming)
            var direction = 1;
        $.ajax({
            url: url,
            data: {
                csrfmiddlewaretoken: csrftoken, 
                category: catname,
                direction: direction
            },
            method: "POST",
            success: function(response) {
                console.log("Category created");
                console.log(JSON.stringify(response));
                if(response.errors.length > 0){
                    processErrors(response.errors);
                }else{
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            },
            error: function(xhr, status, error) {
                console.log("Category creation failed");
            },
            complete: function(xhr, textStatus) {
                $('#createCategoryButton span').addClass('d-none');
            }
        });
    });
});