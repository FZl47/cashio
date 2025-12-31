function _showTour() {
    const tourSteps = [
        {
            name: 'dashboard_intro',
            element: 'h3.page-title',
            popover: {
                title: translate('Welcome to Cashio'),
                description: translate('This application helps you manage petty cash funds, track transactions, and organize documents efficiently. You can monitor your income and expenses, view recent transactions, manage users, and keep your records well-structured.')
            }
        },
        {
            name: 'expenses_card',
            element: '.expenses_card',
            popover: {
                title: translate('Expenses Overview'),
                description: translate('Here you can see the total invoice amount for the last 30 days, along with weekly and monthly comparisons. The chart visualizes expense trends over time.')
            }
        },
        {
            name: 'income_card',
            element: '.income_card',
            popover: {
                title: translate('Income Overview'),
                description: translate('This section shows your revenue for the last 30 days, with weekly and monthly comparisons. The bar chart provides a visual summary of income trends.')
            }
        },
        {
            name: 'transactions_table',
            element: '.card-full .nk-tb-list',
            popover: {
                title: translate('Recent Transactions'),
                description: translate('Here you can find the latest transactions, including the user, fund, date, reference, amount, status, and type. Quick links allow you to view more details.')
            }
        },
        {
            name: 'recent_documents',
            element: '.col-lg-6 .nk-activity',
            popover: {
                title: translate('Recent Documents'),
                description: translate('All recently uploaded documents are displayed here. You can quickly view document details or create new documents if you have the necessary permissions.')
            }
        },
        {
            name: 'personal_notifications',
            element: '.col-lg-6 .nk-support',
            popover: {
                title: translate('Personal Notifications'),
                description: translate('Your personal notifications are shown here. Each notification indicates if it has been visited or not and provides quick access to details.')
            }
        },
        {
            name: 'users_card',
            element: '.col-lg-5 .nk-tb-list',
            popover: {
                title: translate('Users Overview'),
                description: translate('If you are an admin, you can see the list of users here with their roles. Quick links allow you to view user profiles.')
            }
        },
        {
            name: 'petty_cash_funds',
            element: '.col-lg-7 .nk-tb-list',
            popover: {
                title: translate('Petty Cash Funds'),
                description: translate('This section lists all petty cash funds with their balance, holders, and status. You can view details or check related transactions.')
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
