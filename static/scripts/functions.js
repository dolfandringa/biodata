
if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
};

function updateSelect(obj){
  select=obj.find('select')
  url=select.attr('data-values_url')
  jQuery.ajax({dataType:'json',method:'get',url:url,success:function(data){
    select=jQuery(select);
    data2=new Array();
    for (k in data){
      if(data[k][0]==undefined){
        continue;
      }
      data2.push({id:data[k][0],text:data[k][1]})
    }
    select.select2('destroy');
    select.select2({data:data2});
    if (select.attr('multiple')=='multiple'){
      val=select.val()
      if (val == null){
        val = []
      }
      val.push(data2.last().id)
    }
    else{
      val=data2.last().id
    }
    select.val(val).trigger('change');
  }});
}

function cleanupModalForm(dialog,container){
  contents=dialog.find('iframe').contents();
  contents.find('button').remove();
  contents.find("form").submit(function(e){
    e.preventDefault();
    jQuery.ajax({
      method: "POST",
      url: jQuery(this).attr('action'),
      data: jQuery(this).serialize(),
      success: function(data){
        data=jQuery(data);
        if(data.find('form').length==0){
          updateSelect(container)
          dialog.dialog("close");
        }
        else{
          dialog.find('iframe').contents().children().first().html(data.children().first());
          cleanupModalForm(dialog,container);
        }
      }
    });
    return false;
  });
}

function openWaitDialog(message){
  dialog=jQuery("<div class='modalForm'><div class='content'><div class='icon'></div><span class='message'>" +message+"</span></div></div>");
  jQuery('body').append(dialog);
  dialog.find('.icon').activity({segments: 8, width:4, space: 0, length: 3, color: '#0b0b0b', speed: 1.5});
  dialog = dialog.dialog({
    autoOpen: false,
    width: 400,
    height: 200,
    modal: true
  });
  dialog.dialog("open");
  return dialog;
}

function closeWaitDialog(dialog,message){
  if(message != undefined){
    dialog.find('.message').text(message);
    waittime=3000;
  }
  else{
    waittime = 1;
  }
  setTimeout(function(){
    dialog.dialog("close");
    dialog.remove();
  },waittime);
}

function setModalLinks(container){
  obj=container.container;
  obj.find('a.editlink').click(function(e){
    e.preventDefault();
    container=jQuery(this).parent();
    url=jQuery(this).attr('href');
    d=jQuery("<div class='modalForm'><iframe src='"+url+"'></iframe></div>");
    jQuery('body').append(d);
    d = d.dialog({
      autoOpen: false,
      position: {my: 'center top', at: 'center top'},
      width: 900,
      height: 600,
      modal: true,
      buttons: {
        Save: function(){
          jQuery(this).find("iframe").contents().find("form").submit();
          obsList.refresh();
        }
      }
    });
    d.dialog("open");
    d.find('iframe').load(function(){
      cleanupModalForm(d,container);
    });
    return false;
  });
  obj.find('a.addlink').click(function(e){
    container=jQuery(this).parent()
    url=jQuery(this).attr('href')
    dialog=jQuery("<div class='modalForm'><iframe src='"+url+"'></iframe></div>");
    jQuery('body').append(dialog);
    dialog = dialog.dialog({
      autoOpen: false,
      position: {my: 'center top', at: 'center top'},
      width: 400,
      height: 400,
      modal: true,
      buttons: {
        Save: function(){
          jQuery(this).find("iframe").contents().find("form").submit();
        }
      }
    });
    dialog.dialog("open");
    dialog.find('iframe').load(function(){
      cleanupModalForm(dialog,container);
    });
    return false;
  });
  obj.find('a.deletelink').click(function(e){
    url=jQuery(this).attr('href')
    dialog=openWaitDialog('Just a moment please.')
    jQuery.get(url,function(){
      closeWaitDialog(dialog);
      obsList.refresh()
    });
    return false;
  });

}
