function tabView(parent, contents) {
    // Parent customization:
    parent.classed('tab-view', true)
          .style('overflow-x', 'hidden');

    // The scroll buttons:
    parent.append('p').attr('id', 'left-button')
                      .classed('scroll', true)
                      .style('display', 'none')
                      .text('<');
    parent.append('p').attr('id', 'right-button')
                      .classed('scroll', true)
                      .style('display', 'none')
                      .text('>');

    // The tabs:
    var tabBar = parent.append('ul');
    var tabElements = tabBar.selectAll('li').data(contents.querySelectorAll('div'));
    tabElements.exit().remove();
    tabElements = tabElements.enter().append('li').text((d) => d.title).merge(tabElements);

    // The pages:
    var page = parent.append('div');
    contents.querySelectorAll('div').forEach(function(d) {
        var newPage = page.append(() => d);
        drawGraphs(newPage);
    });
    page.selectAll('div').style('display', 'none');

    // Tabs and pages binding:
    tabElements.on('click', (d, i) => {
        page.selectAll('div').filter(function() {
            return d3.select(this).style('display') == 'block';
        }).dispatch('hide');
        tabElements.classed('active-tab', false);
        page.selectAll('div').style('display', 'none');
        tabElements.filter((d, j) => (i == j)).classed('active-tab', true);
        page.selectAll('div').filter((d, j) => (i == j)).style('display', 'block')
                                                        .dispatch('show');
        this.windowResize();
    });
    tabElements.filter((d, i) => (i == 0)).classed('active-tab', true);
    page.selectAll('div').filter((d, i) => (i == 0)).style('display', 'block');

    // Scroll:
    this.scroll = function(dir) {
        var curMargin = parseFloat(tabBar.style('margin-left'));
        var pw = tabBar.node().getBoundingClientRect().width + curMargin + 4;

        var tw = -8;
        tabElements.each(function() {
           tw += this.getBoundingClientRect().width;
        });

        //console.log("Scroll: ", pw - 30 - tw, curMargin, 26);

        tabBar.style('margin-left', Math.max(pw - 30 - tw, Math.min(26, curMargin + dir)) + 'px');
    };
    this.autoScroll = (function() {
        var scrollTimer = null;
        return function(start, dir) {
            if (start) {
                this.scroll(dir);
                scrollTimer = window.setInterval(() => this.scroll(dir), 100);
            } else {
                if (scrollTimer !== null)
                    window.clearInterval(scrollTimer);
                scrollTimer = null;
            }
        };
    }).call(this);

    parent.select('#left-button').on('mousedown', () => this.autoScroll(true, +5));
    parent.select('#left-button').on('mouseup', () => this.autoScroll(false));
    parent.select('#right-button').on('mousedown', () => this.autoScroll(true, -5));
    parent.select('#right-button').on('mouseup', () => this.autoScroll(false));

    // Resize event:
    this.windowResize = function() {
        var curMargin = parseFloat(tabBar.style('margin-left'));
        var pw = tabBar.node().getBoundingClientRect().width + curMargin + 4;

        var tw = -8;
        var bw = -8;
        var aw = -8;
        tabElements.each(function() {
           if (d3.select(this).classed('active-tab'))
               bw = tw;
           tw += this.getBoundingClientRect().width;
           if (d3.select(this).classed('active-tab'))
               aw = tw;
        });

        // console.log("Total width:", tw);
        // console.log("Before width:", bw);
        // console.log("After width:", aw);
        // console.log("Parent width:", pw);


        if (pw < tw) {
            parent.selectAll('.scroll').style('display', 'block');

            var maxMargin = Math.min(26, pw - 30 - aw);
            var minMargin = Math.max(pw - 30 - tw, 26 - 8 - bw);

            // console.log("Margins:", minMargin, curMargin, maxMargin);

            tabBar.style('margin-left', Math.max(minMargin, Math.min(maxMargin, curMargin)) + 'px');
        } else {
            parent.selectAll('.scroll').style('display', 'none');
            tabBar.style('margin-left', '-4px');
        }
    };

    d3.select(window).on('resize.tab-view', this.windowResize.bind(this));
    parent.on('close', function() {
        console.log("Tab-view close event");
        page.selectAll('div').dispatch('close');
        d3.select(window).on('resize.tab-view', null);
    });
    this.windowResize();
}
