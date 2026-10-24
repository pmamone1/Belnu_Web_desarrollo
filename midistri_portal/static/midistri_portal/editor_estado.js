(function(g){'use strict';const clone=x=>JSON.parse(JSON.stringify(x));let seq=0;
class EditorState{
 constructor(datos,revision,send){this.datos=clone(datos);this.revision=revision;this.send=send;this.dirty=false;this.blocked=false;this.back=[];this.forward=[];this.flight=null;this.pending=null;this.locked=false;}
 change(fn){if(this.locked)return;this.back.push(clone(this.datos));if(this.back.length>60)this.back.shift();this.forward=[];fn(this.datos);this.dirty=true;}
 undo(){if(this.locked||!this.back.length)return;this.forward.push(clone(this.datos));this.datos=this.back.pop();this.dirty=true;}
 redo(){if(this.locked||!this.forward.length)return;this.back.push(clone(this.datos));this.datos=this.forward.pop();this.dirty=true;}
 freeze(){this.locked=true;}
 unfreeze(){this.locked=false;}
 marker(){return JSON.stringify([this.revision,this.datos]);}
 matches(m){return !this.dirty&&!this.flight&&this.marker()===m;}
 acceptUpload(ack,expected){if(ack.revision!==expected+1)throw Error('La revisión cambió durante la subida. Recargá conservando tu copia.');this.back.push(clone(this.datos));this.forward=[];this.datos=clone(ack.datos);this.revision=ack.revision;}
 save(){if(this.pending)return this.pending;if(this.blocked)return Promise.reject(Error('Otra pestaña cambió el borrador. Guardá tu copia y recargá.'));
 this.pending=this.flush().finally(()=>{this.pending=null;this.locked=false;});return this.pending;}
 async flush(){while(this.dirty||this.flight){if(!this.flight){const uuid=typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():'00000000-0000-4000-8000-'+(++seq+Date.now()).toString(16).padStart(12,'0').slice(-12);this.flight={accion:'guardar',revision:this.revision,operacion:uuid,datos:clone(this.datos)};this.dirty=false;}
 try{const ack=await this.send(this.flight);if(ack.revision!==this.flight.revision+1){const e=Error('El borrador cambió en otra pestaña.');e.status=409;throw e;}this.revision=ack.revision;this.flight=null;}
 catch(e){if(e.status===400){this.flight=null;this.dirty=true;}if(e.status===409)this.blocked=true;throw e;}}
 }
}
g.EditorState=EditorState;
})(globalThis);
