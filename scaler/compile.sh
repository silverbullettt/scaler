if [ ! -d "build" ]; then
 mkdir build
else
 rm -rf build/*
fi

CP="lib/guava-23.0.jar"

javac -classpath $CP $(find src -name "*.java") -d build
jar -cvf scaler.jar -C build .
mv scaler.jar build
