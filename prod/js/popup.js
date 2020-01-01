function Popup() {
    // Argument processing (contents[, title[, icon, [buttons]]])
    if (arguments.length < 1)
        return;

    var contents = arguments[0];
    var title = null;
    var icon = null;
    var buttons = [];

    if (arguments.length >= 2)
        title = arguments[1];
    if (arguments.length >= 3)
        icon = arguments[2];
    if (arguments.length >= 4)
        buttons = arguments[3].reverse();

    // The overlay:
    var overlay = d3.select('body').append('div').classed('overlay', true);

    // The popup:
    var popup = d3.select('body').append('div').classed('popup', true)
                                               .style('display', 'none')
                                               .on('click', () => {d3.event.stopPropagation();});

    // The close button:
    var closeButton = popup.append('img').attr('src', 'img/close.png')
                                         .attr('title', 'Fermer')
                                         .attr('alt', 'X')
                                         .attr('id', 'close');

    // Title and icon:
    if (title) {
        popup.append('h4');

        if (icon)
            popup.select('h4').append('img').attr('src', icon);

        popup.select('h4').append('span').text(title);
    }

    // Contents:
    var content = popup.append('div').attr('id', 'content')

    // Buttons:
    if (buttons.length != 0) {
        var buttonBox = popup.append('div').classed('buttonBox', true);
        content.style('bottom','37px');

        buttons.map((d) => {
            buttonBox.append('input').attr('type', 'button')
                                     .attr('title', d.title)
                                     .attr('value', d.title)
                                     .on('click', () => d.callback.bind(this)(content));
        });
    } else {
        content.style('bottom','0px');
    }

    // Show function:
    this.show = function() {
        popup.style('display', null);
    }

    // Close function:
    this.close = function() {
        d3.selectAll('.popup').select('#content').dispatch('close');
        d3.selectAll('.overlay').remove();
        d3.selectAll('.popup').remove();
        d3.select(window).on('keydown.popup', null);
        d3.select(window).on('resize.popup', null);
    };

    // Resize event:
    this.windowResize = function() {
        // Popup width and height:
        var w = window.innerWidth;
        var h = window.innerHeight;

        var pw = Math.max(0.5*w, Math.min(362, w));
        var ph = Math.max(0.7*h, Math.min(462, h));

        popup.style('width', pw + 'px')
             .style('height', ph + 'px')
             .style('left', ((w - pw) / 2) + 'px')
             .style('top', ((h - ph) / 2) + 'px');
    };

    overlay.on('click', this.close.bind(this));
    closeButton.on('click', this.close.bind(this));
    d3.select(window).on('keydown.popup', () => {
        if ((d3.event.key == 'Escape') && !d3.event.shiftKey && !d3.event.altKey && !d3.event.ctrlKey && !d3.event.metaKey)
            this.close();
    });

    contents.bind(this)(content);
    d3.select(window).on('resize.popup', this.windowResize.bind(this));
    this.windowResize();
}
