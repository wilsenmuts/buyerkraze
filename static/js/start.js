function handlePreviousSelection1(selected) {
    if (confirm(`You previously selected ${selected}. Do you want to proceed with this or choose a new country?`)) {
        // Proceed with previous
        window.location.href = `/redirect?country=${selected}`;  // Adjust if needed; for simplicity, form handles
    } else {
        // Choose new; form is already there
    }
}