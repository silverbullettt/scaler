package ptatoolkit.scaler.doop;

import ptatoolkit.doop.basic.DoopObj;
import ptatoolkit.doop.factory.ElementFactory;
import ptatoolkit.pta.basic.Obj;

public class ObjFactory extends ElementFactory<Obj> {

    @Override
    protected Obj createElement(String name) {
        return new DoopObj(name, null, ++count);
    }
}
