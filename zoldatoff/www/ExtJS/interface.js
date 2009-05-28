/**
 * @author dsoldatov
 */
Ext.onReady(function(){

    Ext.state.Manager.setProvider(new Ext.state.CookieProvider());
    
    var viewport = new Ext.Viewport({
        layout: 'border',
        items: [new Ext.BoxComponent({
            region: 'north',
            el: 'north',
            height: 32
        }), {
            region: 'south',
            //contentEl: 'south',
            title: 'Gallery: Squirells',
            //split: true,
            height: 185,
            collapsible: true,
            margins: '0 0 0 0',
            layout: 'column',
            items: [{
                region: 'toLeft',
                contentEl: 'divLeft',
                width: 25,
				border: false
            }, {
                region: 'center',
                contentEl: 'south',
                border: false,
                columnWidth: 1.0
            }, {
                region: 'toRight',
                contentEl: 'divRight',
                width: 25,
				border: false
            }]
        }, {
            region: 'west',
            contentEl: 'west',
            title: 'West',
            id: 'left',
            split: true,
            width: 200,
            minSize: 175,
            maxSize: 400,
            collapsible: true,
            margins: '0 0 0 5',
            layout: 'accordion',
            layoutConfig: {
                animate: true
            },
            items: [{
                //contentEl: 'west',
                title: 'Портреты',
                html: '<a href=javascript:loadAlbum("Win");>Win</a>',
                border: false
            }, {
                title: 'Пейзажи',
                html: '<a href=javascript:loadAlbum("squirell");>Белки!</a>',
                border: false
            }, {
                title: 'Концерты',
                html: '<a href=javascript:loadAlbum("Wallpaper");>Wallpaper</a>',
                border: false
            }]
        }, {
            region: 'center',
            contentEl: 'center',
            title: 'Squirell',
            margins: '0 0 0 0'
        }]
    });
    
    /*
     Ext.get("hideit").on('click', function() {
     var w = Ext.getCmp('left');
     w.collapsed ? w.expand() : w.collapse();
     });
     */
    // Рисуем заставку
    var gifImage = document.getElementById("loading-img");
    gifImage.src = "img/loader_2_222.gif";
    
    innerDiv = document.getElementById("inner-loading");
    outerDiv = document.getElementById("outer-loading");
    outerDiv.onclick = function(){
        this.className = "loading-invisible";
    }
    setTimeout('outerDiv.onclick()', 3000);
    
    gifImage.onload = function(){
        var innerX = gifImage.width;
        var innerY = gifImage.height;
        
        innerDiv.style.left = (window.innerWidth - innerX) / 2 + 'px';
        innerDiv.style.top = (window.innerHeight - innerY) / 2 + 'px';
        innerDiv.style.position = 'absolute';
    }
    
    loadAlbum();
});
