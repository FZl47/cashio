function _showTour() {
    const tourSteps = [
        {
            name: 'transaction_header',
            element: 'h3.page-title',
            popover: {
                title: translate('Transaction Detail'),
                description: translate('Here you can see the full details of the selected petty cash transaction, including reference number, fund, holder, type, amount, date, and description.')
            }
        },
        {
            name: 'basic_info',
            element: '.col-12.col-lg-6 .nk-block-title.title',
            popover: {
                title: translate('Basic Information'),
                description: translate('This section shows the main details of the transaction such as fund, holder, creator, type, amount, reference number, transaction date, creation date, and description.')
            }
        },
        {
            name: 'statuses',
            element: '.statuses-box',
            popover: {
                title: translate('Statuses'),
                description: translate('All statuses related to this transaction are displayed here. You can see who created each status, its type (approved, rejected, pending), notes, and creation date.')
            }
        },
        {
            name: 'create_status_button',
            element: '.btn-create-status',
            popover: {
                title: translate('Create Status'),
                description: translate('You can create a new status for this transaction using this button.')
            }
        },
        {
            name: 'attached_files',
            element: '.attached-files-box',
            popover: {
                title: translate('Attached Files'),
                description: translate('All files attached to this transaction are displayed here. You can view or download them. If permitted, you can also add new files.')
            }
        },
        {
            name: 'add_file_button',
            element: '.btn-attach-file',
            popover: {
                title: translate('Add File'),
                description: translate('Click this button to attach a new file to the transaction. Supported formats include PDF, JPG, PNG, DOC, XLS, etc.')
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
