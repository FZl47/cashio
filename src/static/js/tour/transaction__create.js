function _showTour() {
    const tourSteps = [
        {
            name: 'create_transaction_header',
            element: 'h3.page-title',
            popover: {
                title: translate('Create Transaction'),
                description: translate('This page allows you to create a new petty cash transaction. Fill in the required information and attach files if necessary.')
            }
        },
        {
            name: 'transaction_info_card',
            element: '.card-title',
            popover: {
                title: translate('Transaction Information'),
                description: translate('Enter all relevant details for the transaction including fund, holder, type, amount, reference number, date, attached files, and description.')
            }
        },
        {
            name: 'fund_field',
            element: '#fund',
            popover: {
                title: translate('Petty Cash Fund'),
                description: translate('Select the petty cash fund for this transaction.')
            }
        },
        {
            name: 'holder_field',
            element: '#holder',
            popover: {
                title: translate('Holder'),
                description: translate('Choose the holder of the selected fund. If you are not an admin, this field may be disabled.')
            }
        },
        {
            name: 'transaction_type_field',
            element: '#transaction_type',
            popover: {
                title: translate('Transaction Type'),
                description: translate('Select whether this transaction is an income or an expense.')
            }
        },
        {
            name: 'amount_field',
            element: '#amount',
            popover: {
                title: translate('Amount'),
                description: translate('Enter the amount for this transaction in numbers.')
            }
        },
        {
            name: 'reference_number_field',
            element: '#reference_number',
            popover: {
                title: translate('Reference Number'),
                description: translate('Optionally, enter a reference number for this transaction.')
            }
        },
        {
            name: 'date_field',
            element: '#date',
            popover: {
                title: translate('Transaction Date'),
                description: translate('Pick the date of the transaction. The format is Day-Month-Year.')
            }
        },
        {
            name: 'attach_file_field',
            element: '#attach_file',
            popover: {
                title: translate('Attach File'),
                description: translate('You can attach receipts, invoices, or other relevant files. Multiple files can be selected.')
            }
        },
        {
            name: 'description_field',
            element: '#description',
            popover: {
                title: translate('Description'),
                description: translate('Optionally, enter additional details about the transaction.')
            }
        },
        {
            name: 'submit_button',
            element: '.btn.btn-lg.btn-primary',
            popover: {
                title: translate('Create Transaction Submit'),
                description: translate('Click this button to submit the transaction and save it.')
            }
        }
    ];


    const _driverMenuObj = window.driver.js.driver({
        showProgress: true,
        steps: tourSteps,
        nextBtnText: translate('next'),
        prevBtnText: translate('previous'),
        doneBtnText: translate('done'),

    });

    _driverMenuObj.drive();
}
