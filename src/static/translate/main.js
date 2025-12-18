const fa_lang = {
    'This Field is Required': 'این فیلد الزامی است',
    'Expense': 'هزینه',
    'Income': 'درامد',
    'Creditor': 'بستانکار',
    'Debtor': 'بدهکار',
    'Rial': 'ریال'
}


const en_lang = {
    'This Field is Required': null,
}


const it_lang = {
    'This Field is Required': 'Questo campo è obbligatorio.',
    'Expense': 'Costo',
    'Income': 'Reddito',
    'Creditor': 'Creditore',
    'Debtor': 'Debitore',
}


const _langs = {
    'fa': fa_lang,
    'en': en_lang,
    'it': it_lang,
}


function get_lang_messages_file(lang_code) {
    return _langs[lang_code]
}

function translate(text) {
    let m = get_lang_messages_file(LANGUAGE_CODE)
    let t = m[text] || text
    return t
}
