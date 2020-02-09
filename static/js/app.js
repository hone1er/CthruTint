
document.getElementById("yes-referred").addEventListener("click", referred);
document.getElementById("no-referred").addEventListener("click", notReferred);


    function referred() {
      document.getElementById('referred-block').style.display = 'block';
    }

    function notReferred() {
        document.getElementById('referred-block').style.display = 'none';
    }