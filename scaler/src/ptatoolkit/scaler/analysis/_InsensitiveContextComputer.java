package ptatoolkit.scaler.analysis;

import ptatoolkit.pta.basic.Method;
import ptatoolkit.scaler.pta.PointsToAnalysis;

/**
 * Context-insensitive analysis can be seen as the analysis where
 * all contexts are merged as 1 context.
 */
public class _InsensitiveContextComputer extends ContextComputer {

    public _InsensitiveContextComputer(PointsToAnalysis pta) {
        super(pta, null);
    }

    @Override
    public String getAnalysisName() {
        return "context-insensitive";
    }

    @Override
    protected int computeContextNumberOf(Method method) {
        return 1;
    }
}
