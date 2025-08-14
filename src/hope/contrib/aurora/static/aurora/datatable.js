"use strict";

var $table = $("#records");
var $details = $("#details");
var $fromDate = $("#date_start");
var $toDate = $("#date_end");

var registrationId = $table.data("reg");
var baseUrl = `/api/registration/${registrationId}`
var rowPerPage = 30;
var requestVersion = 1;

var showDetails = function (rowid) {
    $details.html("");
    if (rowid !== this.lastSel) {
        var userdata = $table.getGridParam('userData');
        var details = userdata[rowid];
        $details.append(`<div class="text-center">${details["code"]}</div>`)
        for (const key in details) {
            $details.append(`<div class="font-bold">${key}</div>`)
            $details.append(`<div class="mb-3">${details[key]}</div>`)
        }
    }
    this.lastSel = rowid;
}
var buildGrid = function (columns) {
    $table.jqGrid({
        url: `${baseUrl}/records/`,
        edit: true,
        altRows: true,
        autowidth: false,
        rowid: "id",
        caption: "",
        colModel: columns,
        datatype: 'json',
        footerrow: true,
        gridview: true,
        guiStyle: "jQueryUI",
        height: 300,
        hoverrows: true,
        loadonce: false,
        // iconSet: "fontAwesome",
        // multikey: "altKey",
        multiselect: true,
        multiboxonly: true,
        pager: '#dataTablePager',
        pgbuttons: true,
        // pgtext: null,
        prmNames: {nd: null},
        recordpos: 'left',
        rowNum: rowPerPage,
        rownumbers: true,
        rownumWidth: 40,
        viewrecords: true,
        width: 900,
        jsonReader: {
            id: 'id',
            repeatitems: true,
            cell: "cell",
            root: 'results',
            page: 'page',
            records: 'count',
            total: function (obj) {
                return Math.ceil(obj.count / rowPerPage);
            },
            userdata: function (obj) {
                var ret = {};
                for (var i in obj.results) {
                    ret[obj.results[i].id] = obj.results[i].flatten;
                }
                return ret
            }
        },
        serializeGridData: function (postData) {
            var myPostData = $.extend({}, postData); // make a copy of the input parameter
            myPostData._ver = requestVersion;
            myPostData.start_date = $fromDate.val();
            // myPostData._toDate = $toDate.val();
            return myPostData;
        },
        beforeSelectRow: function (rowid, e) {
            $details.html("");
            if ($(e.target).is('input[type=checkbox]')) {
                return true;
            } else {
                $('#' + this.lastSel).removeClass("details");
                if (rowid !== this.lastSel) {
                    $('#' + rowid).addClass("details");
                    var userdata = $table.getGridParam('userData');
                    var details = userdata[rowid];
                    $details.append(`<div class="text-center">${details["code"]}</div>`)
                    for (const key in details) {
                        $details.append(`<div class="font-bold">${key}</div>`)
                        $details.append(`<div class="mb-3">${details[key]}</div>`)
                    }
                    this.lastSel = rowid;
                } else {
                    this.lastSel = null;
                }
                return false;
            }
            // return $(e.target).is('input[type=checkbox]');
        },
        gridComplete: function () {
            $(".ui-th-column").css('white-space', 'normal').css("padding", "1px");
        },
        onSelectRow: function (rowid) {
        },
    });
}// buildGrid

$.ajax({
    url: `${baseUrl}/metadata/`,
    success: function (data) {
        var columns = [
            {name: "id", label: "#", width: "40", align: "right", sortable: false},
            {
                name: "timestamp", label: "Timestamp", formatter: 'date', formatoptions: {newformat: 'Y-m-d'},
                width: "70", sortable: false
            },
            {name: "remote_ip", label: "Remote IP", width: "100", sortable: false},
        ];
        for (var f in data.base.fields) {
            columns.push({
                name: data.base.fields[f].name,
                label: data.base.fields[f].label,
                sortable: false,
            })
        }
        buildGrid(columns);
        $("#refresh").on('click', function(){
            $table.trigger('reloadGrid');
        });
    } // success
});
