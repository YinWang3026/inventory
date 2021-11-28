$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inv_id").val(res.id);
        $("#inv_name").val(res.name);
        $("#inv_quantity").val(res.quantity);
        $("#inv_restock_level").val(res.restock_level);
        $("#inv_condition").val(res.condition);
        $("#inv_need_restock").val("");
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inv_name").val("");
        $("#inv_quantity").val("");
        $("#inv_restock_level").val("");
        $("#inv_condition").val("");
        $("#inv_need_restock").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Inventory
    // ****************************************

    $("#create-btn").click(function () {
        var name = $("#inv_name").val();
        var quantity = parseInt($("#inv_quantity").val(), 10); // Base 10
        var restock_level = parseInt($("#inv_restock_level").val(), 10);
        var condition = $("#inv_condition").val().toLowerCase();

        var data = {
            "name": name,
            "quantity": quantity,
            "restock_level": restock_level,
            "condition": condition
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory
    // ****************************************

    $("#update-btn").click(function () {

        var inv_id = $("#inv_id").val();
        var name = $("#inv_name").val();
        var quantity = parseInt($("#inv_quantity").val(), 10); // Base 10
        var restock_level = parseInt($("#inv_restock_level").val(), 10);
        var condition = $("#inv_condition").val().toLowerCase();

        var data = {
            "name": name,
            "quantity": quantity,
            "restock_level": restock_level,
            "condition": condition
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/inventory/" + inv_id,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {
        var inv_id = $("#inv_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + inv_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete an Inventory
    // ****************************************

    $("#delete-btn").click(function () {

        var inv_id = $("#inv_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/inventory/" + inv_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inv_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for an Inventory
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#inv_name").val();
        var condition = $("#inv_condition").val();
        var need_restock = $("#inv_need_restock").val() == "true";

        var queryString = ""
        if (name) {
            queryString += 'name=' + name
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition.toLowerCase()
            } else {
                queryString += 'condition=' + condition.toLowerCase()
            }
        }
        if (need_restock) {
            if (queryString.length > 0) {
                queryString += '&need_restock=' + need_restock
            } else {
                queryString += 'need_restock=' + need_restock
            }
        }
        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:20%">Name</th>'
            header += '<th style="width:20%">Quantity</th>'
            header += '<th style="width:20%">Restock Level</th>'
            header += '<th style="width:20%">Condition</th>'
            $("#search_results").append(header);
            var firstInv = "";
            for (var i = 0; i < res.length; i++) {
                var inv = res[i];
                var row = "<tr><td>" + inv.id +
                    "</td><td>" + inv.name +
                    "</td><td>" + inv.quantity +
                    "</td><td>" + inv.restock_level +
                    "</td><td>" + inv.condition +
                    "</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstInv = inv;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstInv != "") {
                update_form_data(firstInv)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Add Stock to an Inventory
    // ****************************************

    $("#add-stock-btn").click(function () {

        var inv_id = $("#inv_id").val();
        var add_stock = parseInt($("#inv_add_stock").val(), 10);


        var data = {
            "add_stock": add_stock
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/inventory/" + inv_id + "/add_stock",
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
