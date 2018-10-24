package ptatoolkit.scaler.analysis;

import ptatoolkit.Global;
import ptatoolkit.pta.basic.Method;
import ptatoolkit.scaler.pta.PointsToAnalysis;

public class _1TypeContextComputer extends ContextComputer {

    public _1TypeContextComputer(PointsToAnalysis pta, ObjectAllocationGraph oag) {
        super(pta, oag);
    }

    @Override
    public String getAnalysisName() {
        return "1-type";
    }

    @Override
    protected int computeContextNumberOf(Method method) {
        if (pta.receiverObjectsOf(method).isEmpty()) {
            if (Global.isDebug()) {
                System.out.printf("Empty receiver: %s\n", method.toString());
            }
            return 1;
        }
        return (int) pta.receiverObjectsOf(method).stream()
                .map(pta::declaringAllocationTypeOf)
                .distinct()
                .count();
    }
}
