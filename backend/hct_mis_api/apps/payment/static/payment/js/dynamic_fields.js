document.addEventListener('DOMContentLoaded', (event) => {
  const specialClasses = new Set([
    'field-card_number',
    'field-phone_no',
    'field-bank_name',
    'field-bank_account_number'
  ]);

  const hideSpecialFields = () => {
    const formRows = document.querySelectorAll(".form-row")
    for (const formRow of formRows) {
      for (const className of formRow.classList) {
        if (specialClasses.has(className)) {
          formRow.style.display = 'none'
        }
      }
    }
  };

  const adjustFieldsToMechanism = () => {
    const selectedIdx = deliveryMechanismDropdown.selectedIndex;
    if (deliveryMechanismDropdown.options[selectedIdx].value === 'Deposit to Card') {
      hideSpecialFields();
      document.getElementsByClassName('field-card_number')[0].style.display = 'block';
    } else if (deliveryMechanismDropdown.options[selectedIdx].value === 'Mobile Money') {
      hideSpecialFields();
      document.getElementsByClassName('field-phone_no')[0].style.display = 'block';
    } else if (deliveryMechanismDropdown.options[selectedIdx].value === 'Transfer to Account') {
      hideSpecialFields();
      document.getElementsByClassName('field-bank_name')[0].style.display = 'block';
      document.getElementsByClassName('field-bank_account_number')[0].style.display = 'block';
    } else {
      hideSpecialFields()
    }
  }

  const deliveryMechanismDropdown = document.getElementById("id_delivery_mechanism");

  deliveryMechanismDropdown.addEventListener("change", () => {
    adjustFieldsToMechanism();
  });

  adjustFieldsToMechanism();
});