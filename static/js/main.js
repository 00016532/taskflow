document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            if (window.bootstrap && window.bootstrap.Alert) {
                const bsAlert = window.bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
                return;
            }
            alert.remove();
        });
    }, 4000);
});
