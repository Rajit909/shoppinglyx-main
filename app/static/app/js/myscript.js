$('#slider1, #slider2, #slider3, #slider4, #slider5, #slider6, #slider-related').owlCarousel({
    loop: false,
    margin: 20,
    responsiveClass: true,
    nav: true,
    dots: false,
    navText: ["<i class='fas fa-chevron-left'></i>","<i class='fas fa-chevron-right'></i>"],
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: false,
            autoplay: false,
        }
    }
})

$('.plus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = $(this).siblings('.quantity');
    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            prod_id: id
        },
        success: function (data){
            eml.text(data.quantity)
            $("#amount").text(data.amount.toFixed(2))
            $("#totalamount").text(data.totalamount.toFixed(2))
        }
    })
})

$('.minus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = $(this).siblings('.quantity');
    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            prod_id: id
        },
        success: function (data){
            eml.text(data.quantity)
            $("#amount").text(data.amount.toFixed(2))
            $("#totalamount").text(data.totalamount.toFixed(2))
        }
    })
})

$('.remove-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var node = $(this).closest('.row.mb-4');
    $.ajax({
        type: "GET",
        url: "/removecart",
        data: {
            prod_id: id
        },
        success: function (data){
            $("#amount").text(data.amount.toFixed(2))
            $("#totalamount").text(data.totalamount.toFixed(2))
            node.remove();
            if (data.amount <= 0) {
                window.location.reload(); // Show empty cart if no items left
            }
        }
    })
})

