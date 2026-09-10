function copiarCorreo(event) {
    event.preventDefault();

    const correo = "itindpiloto6@educacionbogota.edu.co";

    navigator.clipboard.writeText(correo)
        .then(() => {
            alert("Correo copiado: " + correo);
        })
        .catch(() => {
            alert("No se pudo copiar el correo");
        });
}

document.addEventListener("DOMContentLoaded", function () {

    let botonMenu = document.getElementById("botonMenu");
    let menu = document.getElementById("menuDesplegable");

    botonMenu.addEventListener("click", function (event) {

        event.preventDefault();

        menu.classList.toggle("mostrar");

    });

});