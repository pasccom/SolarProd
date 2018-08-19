function SolarProd() {
    d3.select('body').append('div');

    var toolbar1 = d3.select('body').select('div').append('div').classed('toolbar', true);
    var toolbar2 = d3.select('body').select('div').append('div').classed('toolbar', true);

    // The selectors:
    this.daySelect = toolbar1.append('select').attr('title', 'Jour')
                                              .attr('disabled', true);
    this.monthSelect = toolbar1.append('select').attr('title', 'Mois')
                                                .attr('disabled', true);
    this.yearSelect = toolbar1.append('select').attr('title', 'Année')
                                               .attr('disabled', true);
    this.varSelect = toolbar1.append('select').attr('title', 'Variable')
                                              .attr('disabled', true);
    this.aggSelect = toolbar1.append('select').attr('title', 'Aggrégation')
                                              .attr('disabled', true);

    // The buttons:
    this.plotButton = toolbar1.append('img').classed('button', true)
                                            .attr('src', 'img/plot.png')
                                            .attr('title', 'Tracer')
                                            .attr('alt', 'Tracer');
    this.prevButton = toolbar2.append('img').classed('button', true)
                                            .classed('disabled', true)
                                            .attr('src', 'img/prev.png')
                                            .attr('title', 'Précédent')
                                            .attr('alt', 'Précédent');
    this.todayButton = toolbar2.append('img').classed('button', true)
                                             .attr('src', 'img/today.png')
                                             .attr('title', 'Aujourd\'hui')
                                             .attr('alt', 'Aujourd\'hui');
    this.nextButton = toolbar2.append('img').classed('button', true)
                                            .classed('disabled', true)
                                            .attr('src', 'img/next.png')
                                            .attr('title', 'Suivant')
                                            .attr('alt', 'Suivant');
    this.exportButton = toolbar2.append('img').classed('button', true)
                                              .classed('disabled', true)
                                              .attr('src', 'img/csv.png')
                                              .attr('title', 'Export CSV')
                                              .attr('alt', 'Export CSV');

    // TODO remove?
    // WARNING Used by test.py
    this.daySelect.attr('id', 'day');
    this.monthSelect.attr('id', 'month');
    this.yearSelect.attr('id', 'year');
    this.varSelect.attr('id', 'var');
    this.aggSelect.attr('id', 'sum');

    this.plotButton.attr('id', 'plot');
    this.prevButton.attr('id', 'prev');
    this.todayButton.attr('id', 'today');
    this.nextButton.attr('id', 'next');
    this.exportButton.attr('id', 'export');

    this.chart = null; // TODO construct chart here
}
