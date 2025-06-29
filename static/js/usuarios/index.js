function listadoDocumentos(){
    $.ajax({
        url: '/users/listar-documentos/',
        method: 'GET',
        dataType: 'json',
        success: function(response){
            console.log(response);
           // $('#listado').html(response);
        },
        error: function(error){
            console.log(error);
        }
    });
}
$(document).ready(function(){
    listadoDocumentos();
});