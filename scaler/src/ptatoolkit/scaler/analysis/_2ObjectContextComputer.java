package ptatoolkit.scaler.analysis;

import ptatoolkit.Global;
import ptatoolkit.pta.basic.Method;
import ptatoolkit.pta.basic.Obj;
import ptatoolkit.scaler.pta.PointsToAnalysis;

import java.util.Set;

public class _2ObjectContextComputer extends ContextComputer {

    public _2ObjectContextComputer(PointsToAnalysis pta, ObjectAllocationGraph oag) {
        super(pta, oag);
    }

    @Override
    public String getAnalysisName() {
        return "2-object";
    }

    @Override
    protected int computeContextNumberOf(Method method) {
        if (pta.receiverObjectsOf(method).isEmpty()) {
            if (Global.isDebug()) {
                System.out.printf("Empty receiver: %s\n", method.toString());
            }
            return 1;
        }
        int count = 0;
        for (Obj recv : pta.receiverObjectsOf(method)) {
            Set<Obj> preds = oag.predsOf(recv);
            if (!preds.isEmpty()) {
                count += preds.size();
            } else {
                // without allocator, back to 1-object
                ++count;
            }
        }
        return count;
    }
}
