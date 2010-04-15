var RemoteUpload = new Class({
	Implements: Options,
	options : {
		upload_url:'',
		form_container:$empty()
	},
	initialize: function(options){
        this.setOptions(options);
		console.log(this.options.form_container);
    },
	createForm : function(type){
		this.clearForm();
		self = this;
		var log = new Element('div',{'id':'log_res'}).inject(this.options.form_container);

		var form = new Element('form',{'action':self.options.upload_url,'enctype':'multipart/form-data','id':'uploadform',"method":"post"});
		
		if(type=='image'){
			var input = new Element('input',{'type':'file','id':'img'});
			var height = new Element('input',{'type':'text','id':'height'});
			var width = new Element('input',{'type':'text','id':'width'});
			form.adopt(input,height,width);
		}else if(type=='blob'){
			var input = new Element('input',{'type':'file','id':'file'});
			form.adopt(input);
		}
		var submit = new Element('input',{'type':'submit','id':'submitter',"name":"button"}).inject(form);
		form.inject(this.options.form_container);
	},
	clearForm : function(){
		this.options.form_container.empty();
	}
});