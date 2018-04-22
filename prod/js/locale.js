// Locale format for dates:
var locale = d3.timeFormatLocale({
  dateTime: "%A %_d %B %Y à %X",
  date: "%d/%m/%Y",
  time: "%H:%M:%S",
  periods: ["AM", "PM"],
  days: ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"],
  shortDays: ["dim", "lun", "mar", "mer", "jeu", "ven", "sam"],
  months: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
  shortMonths: ["jan", "fev", "mar", "avr", "mai", "jun", "jul", "aou", "sep", "oct", "nov", "dec"]
});
var localeLongMonth = locale.format('%B');
var localeShortMonth = locale.format('%b');
