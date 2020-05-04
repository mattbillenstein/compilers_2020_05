use std::cmp::max;

fn maxval(x: &[i32]) -> i32 {
    if x.len() == 1 {
        x[0]
    } else {
        max(x[0], maxval(&x[1..]))
    }
}

#[test]
fn test_maxval() {
    assert!(maxval(&vec![0]) == 0);
    assert!(maxval(&vec![0, 1]) == 1);
    assert!(maxval(&vec![-7, 7, 0, 6]) == 7);
}
